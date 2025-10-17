const determineFontColor = (color) => {
  // Define font colors based on the background color
  switch (color) {
    case "#23A97B": // Green
    case "#C92A2A": // Red
      return "white";
    case "#FED330": // Yellow
    case "#ED9205": // Orange
      return "black";
    default:
      return "black"; // Default font color
  }
};

const colorMap = {
  "green": "#23A97B", // Green
  "yellow": "#FED330", // Yellow
  "orange": "#ED9205", // Orange
  "red": "#C92A2A", // Red
  "violet": "#8A3FFC", // Violet
  "gray": "#CED4DA", // Gray
};


export function generateChartData(
  data,
  periods,
  dayPeriods,
  nightPeriods,
  callsBounds
) {
  // This is assuming that 'callsBounds' is the object fetched from localStorage
  // and passed into this function

  let chartData = periods.map((period, index) => {
    let found = data.find((item) => item.tranche === period);

    // Default values if no data found for the period
    let y = found ? found.value : 0;
    let type = found ? found.type : null;
    let color = found && found.color ? colorMap[found.color] : "#CED4DA";
    let dayNightIndicator = dayPeriods.includes(period)
      ? "day"
      : nightPeriods.includes(period)
      ? "night"
      : "unmatched";


    return {
      id: `point${index}`,
      y: y,
      type: type,
      color: color,
      fontColor: determineFontColor(color),
      reliability: found && found.fiabilite ? found.fiabilite : 0, // Assuming reliability logic remains the same
    };
  });

  return chartData;
}
