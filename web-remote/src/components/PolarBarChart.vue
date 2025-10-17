<template>
  <div class="chart-container">
    <h6 class="chart-title">{{ name }} </h6>
    <q-icon name="mdi-chevron-down" class="chart-icon"></q-icon>
    <highcharts :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';


const props = defineProps({
  data: Array,
  codeGeom: String,
  name: String,
});

const chartOptions = computed(() => ({
  chart: {
    polar: true,
    type: 'column',
    height: "320",
    // backgroundColor: "#e9eaeb72",
    borderRadius: 15,
    shadow: {
      color: 'rgba(0, 0, 0, 0.3)', // Updated shadow color
      offsetX: 0, // Set to 0 for no horizontal offset
      offsetY: 0, // Set to 0 for no vertical offset
      opacity: 1, // Keep the opacity as 1 for full opacity
      width: 5 // Keep the width for the blur effect
    }
  },
  title: {
    text: ""
  },
  legend: {
    enabled: false,
  },
  pane: {
    startAngle: 15,
    endAngle: 375
  },
  tooltip: {
    followPointer: true,
    useHTML: true,
    formatter: function () {
      const pointData = this.point.options;
      return `<table>
        <tr>
          <th colspan="2">Type : ${pointData.type}</th>
        </tr>
        <tr>
          <td style="background-color: ${pointData.color}; color: ${pointData.fontColor}; font-weight: bold">
            Valeur : ${pointData.y}
          </td>
        </tr>
      </table>`;
    }
  },
  xAxis: {
    tickInterval: 30,
    min: 0,
    max: 360,
    labels: {
      formatter: function () {
        let hours = (this.value / 30) * 2 + 1;
        hours = hours > 23 ? hours - 24 : hours;
        return hours + 'H';
      }
    }
  },
  yAxis: {
    endOnTick: false,
    labels: {
      enabled: false
    },
    lineWidth: 0,
    gridLineWidth: 0,
    tickLength: 0
  },
  plotOptions: {
    series: {
      pointStart: 15,
      pointInterval: 30,
    },
    column: {
      pointPadding: 0,
      groupPadding: 0,
      borderWidth: 1,
      borderColor: 'white',
    }
  },
  series: [{
    type: 'column',
    name: 'Values',
    data: props.data.map(item => ({
      y: item.value,
      color: item.color,
      fontColor: item.fontColor,
      type: item.type,
      visible: item.value !== 0
    }))
  }],
  responsive: {
    rules: [{
      condition: {
        maxWidth: 600
      },
      chartOptions: {
        chart: {
          height: '300'
        },
        xAxis: {
          labels: {
            formatter: function () {
              let hours = (this.value / 30) * 2 + 1;
              hours = hours > 23 ? hours - 24 : hours;
              return hours + 'H';
            },
            style: {
              fontSize: '12px'
            }
          }
        }
      }
    }, {
      condition: {
        maxWidth: 400
      },
      chartOptions: {
        chart: {
          height: '250'
        },
        xAxis: {
          labels: {
            formatter: function () {
              let hours = (this.value / 30) * 2 + 1;
              hours = hours > 23 ? hours - 24 : hours;
              return hours + 'H';
            },
            style: {
              fontSize: '12px',
            }
          }
        }
      }
    }, {
      condition: {
        maxWidth: 300
      },
      chartOptions: {
        chart: {
          height: '200'
        },
        xAxis: {
          labels: {
            formatter: function () {
              let hours = (this.value / 30) * 2 + 1;
              hours = hours > 23 ? hours - 24 : hours;
              return hours + 'H';
            },
            style: {
              fontSize: '10px',
            }
          }
        }
      }
    }]
  }
}));

</script>

<style scoped>

.chart-container {
 width: 90%;
 margin: auto;
}

.chart-title {
  color: var(--sad-nightblue);
  font-weight: 600;
  font-size: 1.5em;
  text-align: center;
  margin: 0.75em 0 0 0;
  border-radius: 15px;
}
.chart-icon {
  font-size: 1.75em;
  color: var(--sad-nightblue);
  width: 100%;
}
</style>
