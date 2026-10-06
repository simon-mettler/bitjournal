// `any` is intentional: rules validate different value types and must stay assignable to Rule.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Rule = (value: any) => string | true

export const when =
  (condition: () => boolean, rule: Rule): Rule =>
  (v) =>
    !condition() || rule(v)

export const required =
  (msg = 'Required'): ((v: string | number | null | undefined) => string | true) =>
  (v) =>
    (v !== null && v !== undefined && String(v).trim() !== '') || msg

export const maxLength = (max: number, msg?: string) => (v: string | number | null | undefined) =>
  !v || String(v).length <= max || msg || `Max ${max} characters`

export const isLessThan =
  (getOther: () => number | undefined, msg = 'Must be less than max') =>
  (v: number | undefined) =>
    v == null || getOther() == null || v < (getOther() as number) || msg

export const isMoreThan =
  (getOther: () => number | undefined, msg = 'Must be more than min') =>
  (v: number | undefined) =>
    v == null || getOther() == null || v > (getOther() as number) || msg
