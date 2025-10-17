import { boot } from 'quasar/wrappers'
import Highcharts from 'highcharts'
import HighChartsVue from "highcharts-vue"
import AccessibilityModule from 'highcharts/modules/accessibility'
import ExportingModule from 'highcharts/modules/exporting'
import OfflineExportingModule from 'highcharts/modules/offline-exporting'
import highchartsMore from 'highcharts/highcharts-more';
import AnnotationsModule from 'highcharts/modules/annotations';

AnnotationsModule(Highcharts)
highchartsMore(Highcharts)
AccessibilityModule(Highcharts)
ExportingModule(Highcharts)
OfflineExportingModule(Highcharts)

export default boot(({ app }) => {
  app.use(HighChartsVue)
})
