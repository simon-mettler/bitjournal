// Queue to run board writes one after another.
let queue: Promise<unknown> = Promise.resolve()

export function enqueueBoardWrite<T>(task: () => Promise<T>): Promise<T> {
  const run = queue.then(task)
  queue = run.catch(() => undefined)
  return run
}
