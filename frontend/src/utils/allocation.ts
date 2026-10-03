export function allocation(
  total: number,
  percentages: Record<string, number>,
): Record<string, number> {
  const values = Object.entries(percentages).map(([name, percent]) => ({
    name,
    exact: (total * percent) / 100,
    count: Math.floor((total * percent) / 100),
  }));
  let remaining = total - values.reduce((sum, item) => sum + item.count, 0);
  for (const item of [...values].sort(
    (a, b) =>
      b.exact - b.count - (a.exact - a.count) || a.name.localeCompare(b.name),
  )) {
    if (remaining-- <= 0) break;
    item.count++;
  }
  return Object.fromEntries(values.map(({ name, count }) => [name, count]));
}

export function equalDistribution(names: string[]): Record<string, number> {
  if (!names.length) return {};
  const base = Math.floor(100 / names.length);
  return Object.fromEntries(
    names.map((name, index) => [
      name,
      base + (index < 100 % names.length ? 1 : 0),
    ]),
  );
}

export function defaultDistribution(names: string[]): Record<string, number> {
  const preferred: Record<string, number> = {
    "Mathematics for AI": 5,
    "Data Processing": 10,
  };
  const flexible = names.filter((name) => !(name in preferred));
  if (!flexible.length) return equalDistribution(names);

  const reserved = names.reduce((sum, name) => sum + (preferred[name] ?? 0), 0);
  const remaining = 100 - reserved;
  const base = Math.floor(remaining / flexible.length);
  const extra = remaining % flexible.length;
  let flexibleIndex = 0;
  return Object.fromEntries(
    names.map((name) => {
      if (name in preferred) return [name, preferred[name]];
      const percentage = base + (flexibleIndex < extra ? 1 : 0);
      flexibleIndex += 1;
      return [name, percentage];
    }),
  );
}
