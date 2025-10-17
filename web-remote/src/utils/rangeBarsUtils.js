export function createAlertsChartOptions(data) {
  // Sample data provided by you
  // data = [
  //   {
  //     name: "1",
  //     data: [
  //       { x: "Orages", y: ["2024-09-03T13:00:00", "2024-09-03T21:00:00"] },
  //       { x: "Orages", y: ["2024-09-04T02:00:00", "2024-09-04T09:00:00"] },
  //       {
  //         x: "Precipitations",
  //         y: ["2024-09-03T19:00:00", "2024-09-04T06:00:00"],
  //       },
  //     ],
  //   },
  //   {
  //     name: "2",
  //     data: [
  //       // { x: "Orages", y: ["2024-09-03T13:00:00", "2024-09-03T21:00:00"] },
  //       // { x: "Orages", y: ["2024-09-04T02:00:00", "2024-09-04T09:00:00"] },
  //       {
  //         x: "Orages",
  //         y: ["2024-09-03T21:00:00", "2024-09-04T02:00:00"],
  //       },
  //     ],
  //   },
  // ];

  // Map vigilance levels to specific colors
  const vigilanceColors = {
    "0": "#23a97b", // No vigilance
    "1": "#fed330", // Yellow
    "2": "#ed9205", // Orange
    "3": "#c92a2a", // Red
  };

  // Transform the data and apply colors explicitly
  const seriesData = data.map((series) => ({
    name: series.name,
    data: series.data.map((entry) => ({
      x: entry.x,
      y: [
        new Date(Date.parse(entry.y[0])).getTime(),
        new Date(Date.parse(entry.y[1])).getTime(),
      ],
    })),
  }));

  // Define chart options
  const options = {
    series: seriesData,
    chart: {
      type: "rangeBar",
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: "15%",
        rangeBarGroupRows: true,
        // borderRadius: 7,
      },
    },
    colors: data.map(series => vigilanceColors[series.name]), // Apply vigilance colors based on series name
    fill: {
      type: "solid",
    },
    grid: {
      borderColor: "#181632",
      yaxis: {
        lines: {
          show: false,
        },
      },
    },
    xaxis: {
      type: "datetime",
      axisBorder: {
        show: false,
        color: "#181632",
      },
      axisTicks: {
        show: false,
        color: "#181632",
      },
      labels: {
        datetimeUTC: false,
        align: "center",
        style: {
          colors: "#181632",
          fontFamily: "Roboto, sans-serif",
          fontWeight: "bold",
          fontSize: "12px",
        },
      },
    },
    yaxis: {
      axisBorder: {
        show: true,
      },
      labels: {
        style: {
          colors: "#181632",
          fontFamily: "Roboto, sans-serif",
          fontWeight: "bold",
          fontSize: "14px",
        },
      },
    },
    legend: {
      show: false,
    },
    tooltip: {
      custom: function (opts) {
        const fromDate = new Date(opts.y1);
        const toDate = new Date(opts.y2);

        const fromDayAndTime = fromDate.toLocaleString("fr-FR", {
          day: "2-digit",
          month: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        });

        const toDayAndTime = toDate.toLocaleString("fr-FR", {
          day: "2-digit",
          month: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        });

        const w = opts.ctx.w;
        let ylabel = w.globals.labels[opts.dataPointIndex];

        // Determine the vigilance level
        let seriesName = "";
        switch (w.config.series[opts.seriesIndex].name) {
          case "0":
            seriesName = "Aucune vigilance";
            break;
          case "1":
            seriesName = "Vigilance Jaune";
            break;
          case "2":
            seriesName = "Vigilance Orange";
            break;
          case "3":
            seriesName = "Vigilance Rouge";
            break;
          default:
            seriesName = "";
        }

        const color = w.globals.colors[opts.seriesIndex];

        return (
          '<div class="apexcharts-tooltip-rangebar">' +
          '<div> <span class="series-name" style="color: ' +
          color +
          '">' +
          (seriesName ? seriesName : "") +
          "</span></div>" +
          '<div> <span class="category">' +
          ' </span> <span class="value start-value">' +
          fromDayAndTime +
          '</span> <span class="separator">-</span> <span class="value end-value">' +
          toDayAndTime +
          "</span></div>" +
          "</div>"
        );
      },
    },
  };

  return options;
}

