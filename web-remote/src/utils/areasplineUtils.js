export function formatHistory(data) {
  const colorMap = {
    'INC': "rgb(201, 42, 42)",
    'SAP': "rgb(35, 169, 123)",
    'RTN': "rgb(24, 22, 50)",
    'OD': "rgb(106, 176, 242)",
    'NO': "rgb(237, 146, 5)",
    'AVP': "rgb(64, 64, 122)"
  };
  let series = {};

  data.forEach(point => {
    const date = (new Date(point.creneau)).getTime();
    for (let key in point) {
      if (!['creneau', 'AVP', 'OD','RTN', 'NO'].includes(key)) {
        if (!series[key]) {
          series[key] = {
            name: key,
            data: [],
            color: colorMap[key] || getRandomColor() // Assign a color from the map or a random color if not specified
          };
        }
        series[key].data.push({
          x: date,
          y: parseInt(point[key]),
          fillColor: series[key].color // Use the assigned color for the point's fillColor
        });
      }
    }
  });

  // Sort the data in each series by the x value (date)
  for (let key in series) {
    series[key].data.sort((a, b) => a.x - b.x);
  }

  return Object.values(series);
}
export function formatPredictions(predictionsData, historicalSeries, latestTimestamp) {
  const colorMap = {
    'INC': "rgb(201, 42, 42)",
    'CIS': "rgb(201, 42, 42)", // Map 'CIS' to 'INC'
    'SAP': "rgb(35, 169, 123)",
    'RTN': "rgb(24, 22, 50)",
    'OD': "rgb(106, 176, 242)",
    'NO': "rgb(237, 146, 5)",
    'AVP': "rgb(64, 64, 122)"
  };

  // Map series names to series objects for easy access
  const seriesMap = {};
  historicalSeries.forEach(series => {
    seriesMap[series.name] = series;
  });


  // Round the latest timestamp to the next hour
  const latestDate = new Date(latestTimestamp);
  latestDate.setMinutes(0, 0, 0); // Reset minutes, seconds, milliseconds
  latestDate.setHours(latestDate.getHours() + 1); // Move to the next hour
  const baseTimestamp = latestDate.getTime();

  // Create future timestamps corresponding to horizons: 2h, 4h, ..., 12h
  const horizons = [2, 4, 6, 8, 10, 12]; // in hours
  const futureTimes = horizons.map(hours => baseTimestamp + hours * 3600000); // Convert hours to milliseconds

  // Filter predictions for 'SAP' and 'CIS' (mapped to 'INC')
  const filteredPredictions = predictionsData.filter(item => ['SAP', 'INC'].includes(item.type_interv));

  // Append predictions to the historical series
  filteredPredictions.forEach(prediction => {
    const { type_interv, liste } = prediction;
    const series = seriesMap[type_interv];

    if (!series) return; // Skip if no corresponding historical series

    // Build prediction data points
    const predictionData = liste.map((value, index) => ({
      x: futureTimes[index],
      y: value,
      fillColor: colorMap[type_interv] || getRandomColor(),
    }));

    // Append prediction data to the historical series
    series.data = series.data.concat(predictionData);

    // Add zones to change dash style after the latest timestamp
    series.zoneAxis = 'x';
    series.zones = [{
      value: latestTimestamp + 1, // Up to the latest historical timestamp
      dashStyle: 'Solid'
    }, {
      dashStyle: 'Dash' // Predictions will be dashed
    }];
  });
}


function getRandomColor() {
  const r = Math.floor(Math.random() * 256);
  const g = Math.floor(Math.random() * 256);
  const b = Math.floor(Math.random() * 256);
  return `rgb(${r}, ${g}, ${b})`;
}

export function formatEpidemics(data) {
  let series = {};

  data.forEach(point => {
    const date = (new Date(point.date_data)).getTime();
    const attribut = point.attribut;
    if (!series[attribut]) {
      series[attribut] = {
        name: attribut,
        data: []
      };
    }
    series[attribut].data.push({
      x: date,
      y: point.value
    });
  });

  // Sort the data for each series by date (x value)
  Object.values(series).forEach(serie => {
    serie.data.sort((a, b) => a.x - b.x);
  });

  return Object.values(series);
}

