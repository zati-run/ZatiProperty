"""Durable one-shot Loom authoring utility; never retries an uncertain write."""
import hashlib,json,os,pathlib

def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"))
def sha(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def sync_write(path,value,exclusive=False):
    with path.open("x" if exclusive else "w") as f:
        os.chmod(path,0o600);f.write(canonical(value));f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def dispatch_once(client,name,args,journal,before,read_after,verify):
    """Caller supplies discovered tool, reviewed exact payload and native validators.

    Existing journal is an unconditional fence, including a prior successful run.
    Read state and inspect journal; never blindly replay or delete the fence.
    """
    journal=pathlib.Path(journal)
    intent={"state":"pending-or-unknown","tool":name,"arguments":args,"before":before,"beforeHash":sha(before)}
    sync_write(journal,intent,True)
    try:
        response=client.call(name,args)
        sync_write(journal.with_suffix(journal.suffix+".returned"),{"intentHash":sha(intent),"response":response},True)
        after=read_after()
        if not verify(after):raise RuntimeError("native readback mismatch")
    except Exception as error:
        # Private diagnostic evidence never clears the original no-replay fence.
        sync_write(journal.with_suffix(journal.suffix+".failed"),{"intentHash":sha(intent),"errorType":type(error).__name__,"error":str(error)},True)
        raise
    result={**intent,"state":"verified","response":response,"after":after,"afterHash":sha(after)}
    temp=journal.with_suffix(journal.suffix+".verified")
    sync_write(temp,result,True);os.replace(temp,journal)
    fd=os.open(journal.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return result
