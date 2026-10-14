/* Dictionaries · Python runner.
   Learner code runs here, in the learner's own browser, inside a Web Worker with Pyodide (CPython compiled to WebAssembly).
   It never runs on the server. The page terminates this worker if a run takes too long (infinite loops). */
// Prefer the copy served by this app (works on a classroom network with no internet); fall back to the CDN.
const LOCAL = '/static/vendor/pyodide/', CDN = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
let INDEX = LOCAL;
try { importScripts(LOCAL + 'pyodide.js'); } catch (e) { INDEX = CDN; importScripts(CDN + 'pyodide.js'); }

const RUNNER = `
import sys, json

class _Out:
    LIMIT = 100_000
    def __init__(self):
        self.parts, self.size = [], 0
    def write(self, s):
        self.size += len(s)
        if self.size > self.LIMIT:
            raise RuntimeError("Too much output (over 100,000 characters). Check for a runaway loop.")
        self.parts.append(s)
        return len(s)
    def flush(self):
        pass

def __run(code, stdin):
    feed = iter(stdin.split("\\n"))
    out = _Out()
    def _input(prompt=""):
        out.write(str(prompt))
        try:
            return next(feed)
        except StopIteration:
            raise EOFError("EOF when reading a line: your code called input() more times than there are input lines")
    env = {"__name__": "__main__", "input": _input}
    old, sys.stdout = sys.stdout, out
    err = None
    try:
        exec(compile(code, "main.py", "exec"), env)
    except BaseException as e:
        line = getattr(e, "lineno", None) if isinstance(e, SyntaxError) else None
        tb = e.__traceback__
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == "main.py":
                line = tb.tb_lineno
            tb = tb.tb_next
        err = {"type": type(e).__name__, "msg": str(e), "line": line}
    finally:
        sys.stdout = old
    return json.dumps({"stdout": "".join(out.parts), "error": err})
`;

let py = null;
loadPyodide({ indexURL: INDEX })
  .catch(e => { if (INDEX === CDN) throw e; INDEX = CDN; importScripts(CDN + 'pyodide.js'); return loadPyodide({ indexURL: CDN }); })
  .then(p => { py = p; py.runPython(RUNNER); postMessage({ type: 'ready' }); })
  .catch(e => postMessage({ type: 'loadError', msg: String(e && e.message || e) }));

onmessage = e => {
  const { id, code, stdin } = e.data;
  if (!py) { postMessage({ type: 'result', id, stdout: '', error: { type: 'NotReady', msg: 'Python is still loading.' } }); return; }
  try {
    const r = JSON.parse(py.globals.get('__run')(String(code), String(stdin || '')));
    postMessage({ type: 'result', id, stdout: r.stdout, error: r.error });
  } catch (err) {
    postMessage({ type: 'result', id, stdout: '', error: { type: 'InternalError', msg: String(err) } });
  }
};
