export const calculateScenario = (controls: { recycled: number; renewable: number; transport: number; waste: number; efficiency: number }) => {
  const reductions = controls.recycled * 0.25 + controls.renewable * 0.22 + controls.transport * 0.08 + controls.waste * 0.06 + controls.efficiency * 0.19;
  const reduction = Math.min(4500, Math.round(10000 * reductions / 100));
  const emissions = 10000 - reduction;
  const cost = Math.round(controls.recycled * 5000 + controls.renewable * 3200 + controls.transport * 1800 + controls.waste * 900 + controls.efficiency * 3500);
  return { emissions, reduction, reductionPercent: Math.round((reduction / 10000) * 100), cost, roi: cost ? (reduction / cost).toFixed(3) : "—" };
};

export const calculateEmissionIntensity = (emissions: number, production = 24000) => (emissions / production).toFixed(2);
