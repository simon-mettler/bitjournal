const POINTER_GAP = 16

interface TooltipSize {
  contentSize: [number, number]
  viewSize: [number, number]
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), Math.max(max, min))
}

// Places the tooltip so it doesn't sit under a finger
export function tooltipBesidePointer(
  point: [number, number],
  _params: unknown,
  _dom: unknown,
  _rect: unknown,
  size: TooltipSize,
): [number, number] {
  const [width, height] = size.contentSize
  const [viewWidth, viewHeight] = size.viewSize
  const onRightHalf = point[0] > viewWidth / 2
  const x = onRightHalf ? point[0] - width - POINTER_GAP : point[0] + POINTER_GAP
  const y = point[1] - height - POINTER_GAP
  return [clamp(x, 0, viewWidth - width), clamp(y, 0, viewHeight - height)]
}
