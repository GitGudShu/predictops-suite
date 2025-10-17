export function createChartOptions(rawData) {
  const daysMap = {
    Mon: "lundi",
    Tue: "mardi",
    Wed: "mercredi",
    Thu: "jeudi",
    Fri: "vendredi",
    Sat: "samedi",
    Sun: "dimanche",
  };

  function formatDateString(dateStr) {
    const date = new Date(dateStr);
    const dayName = daysMap[date.toUTCString().substring(0, 3)];
    const day = date.getUTCDate().toString().padStart(2, "0");
    const month = (date.getUTCMonth() + 1).toString().padStart(2, "0");
    return `${dayName} ${day}/${month}`;
  }

  // Sorting the data by 'date_data' field in ascending order
  const sortedData = rawData.sort((a, b) => new Date(a.date_data) - new Date(b.date_data));

  // Group data by formatted date and horizon
  const groupedData = sortedData.reduce((acc, item) => {
    const formattedDate = formatDateString(item.date_data);
    const horizonSuffix = item.horizon === 'Jour' ? 'day' : 'night';

    if (!acc[formattedDate]) {
      acc[formattedDate] = { predit_day: [], predit_night: [], moyenne_day: [], moyenne_night: [] };
    }

    // Always push the predit value to the predit series
    acc[formattedDate][`predit_${horizonSuffix}`].push(item.value);

    // Always push the moyenne value to the moyenne series
    acc[formattedDate][`moyenne_${horizonSuffix}`].push(item.moyenne);

    return acc;
  }, {});


  // Populate series data
  const seriesData = {
    predit_day: [],
    predit_night: [],
    moyenne_day: [],
    moyenne_night: []
  };

  for (const date in groupedData) {
    seriesData.predit_day.push(groupedData[date].predit_day[0] || null);
    seriesData.predit_night.push(groupedData[date].predit_night[0] || null);
    seriesData.moyenne_day.push(groupedData[date].moyenne_day[0] || null);
    seriesData.moyenne_night.push(groupedData[date].moyenne_night[0] || null);
  }

  // Create the series for the chart
  const series = [
    {
      name: "Prédit - Jour",
      data: seriesData.predit_day,
      group: "predit",
      color: "#181632"
    },
    {
      name: "Prédit - Nuit",
      data: seriesData.predit_night,
      group: "predit",
      color: "#181632"
    },
    {
      name: "Moyenne - Jour",
      data: seriesData.moyenne_day,
      group: "moyenne",
      color: "#ced4da"
    },
    {
      name: "Moyenne - Nuit",
      data: seriesData.moyenne_night,
      group: "moyenne",
      color: "#ced4da"
    },
  ];

  // Define the chart options
  return {
    series: series,
    chart: {
      type: "bar",
      stacked: true,
    },
    xaxis: {
      categories: Object.keys(groupedData),
      tickPlacement: "between",
    },
    fill: {
      opacity: 1,
    },
    legend: {
      show: false,
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: function (val) {
          return val;
        }
      }
    },
    states: {
      hover: {
          filter: {
              type: 'none',
          }
      },
  },
  responsive: [{
    breakpoint: 800,

    options: {
      xaxis: {
        categories: Object.keys(groupedData).map(dateStr => dateStr.split(' ')),
      },
      plotOptions: {
        bar: {
          horizontal: true
        }
      },
      dataLabels: {
        enabled: true,
        formatter: function (val, opts) {
          const horizon = opts.w.config.series[opts.seriesIndex].name.includes('Jour') ? 'Jour' : 'Nuit';
          return `${horizon} ${val}`;
        }
    },
  }
}],
    dataLabels: {
      enabled: true,
      formatter: function (val, opts) {
        const horizon = opts.w.config.series[opts.seriesIndex].name.includes('Jour') ? 'Jour' : 'Nuit';
        return [horizon, val];
      },
      dropShadow: {
        enabled: true,
        top: 1,
        left: 1,
        blur: 1,
        color: '#000',
        opacity: 0.65
    }
    },
  };
}
