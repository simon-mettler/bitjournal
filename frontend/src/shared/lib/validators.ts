export type Rule = (value: any) => string | true

export const when = (condition: () => boolean, rule: Rule): Rule =>
  v => !condition() || rule(v)

export const required = (msg = 'Required'): ((v: any) => string | true) =>
  v => (v !== null && v !== undefined && String(v).trim() !== '') || msg

export const maxLength = (max: number, msg?: string) =>
  (v: any) => !v || String(v).length <= max || msg || `Max ${max} characters`

export const isLessThan = (getOther: () => number | undefined, msg = 'Must be less than max') =>
  (v: number | undefined) => v == null || getOther() == null || v < (getOther() as number) || msg

export const isMoreThan = (getOther: () => number | undefined, msg = 'Must be more than min') =>
  (v: number | undefined) => v == null || getOther() == null || v > (getOther() as number) || msg
