export function lineData(values: (number | null)[], markAll = false) {
  return values.map((value, i) => {
    const isolated =
      value !== null && (values[i - 1] ?? null) === null && (values[i + 1] ?? null) === null
    return { value, itemStyle: { opacity: markAll || isolated ? 1 : 0 } }
  })
}

export const lineSymbolOptions = {
  symbol: 'circle',
  showSymbol: true,
  showAllSymbol: true,
  emphasis: { itemStyle: { opacity: 1 } },
}
