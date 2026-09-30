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
  const base = Math.floor(100 / names.length);
  return Object.fromEntries(
    names.map((name, index) => [
      name,
      base + (index < 100 % names.length ? 1 : 0),
    ]),
  );
}
