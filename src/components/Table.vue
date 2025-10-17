<template>
  <div class="table-container">
    <div class="table-controls">
      <q-btn size="sm" color="primary" label="Télécharger CSV" icon="mdi-file-download-outline" @click="downloadCsv"></q-btn>
    </div>
    <div class="table-scroll">
      <div v-if="loading" class="absolute-full flex flex-center">
        <q-spinner-tail size="100px" color="secondary" />
      </div>
      <table class="border-none" v-if="data && !loading">
        <thead>
          <tr>
            <th v-for="column in normalizedColumns" :key="column.field" @click="toggleSort(column.field)">
              {{ column.label }}
              <q-icon v-if="sortColumn === column.field"
                :name="sortOrder === 'asc' ? 'mdi-sort-ascending' : 'mdi-sort-descending'" size="1.25em"
                :style="{ marginLeft: '5px' }">
              </q-icon>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedData" :key="item.nom+'_'+item.fonction"
            :style="{ backgroundColor: getRowColor(item.fonction).bgc, color: getRowColor(item.fonction).fc }">
            <td v-for="column in normalizedColumns" :key="column.field">{{ item[column.field] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
  <div class="flex flex-center" v-if="data">
    <q-pagination v-model="currentPage" :max="maxPages" direction-links boundary-links :boundary-links="false" input />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';

const props = defineProps({
  data: Array,
  loading: Boolean,
  columns: Array,
  excludeColumns: {
    type: Array,
    default: () => []
  },
  rowsPerPage: {
    type: Number,
    default: 7,
  }
})

const currentPage = ref(1)
const maxPages = computed(() => Math.ceil(props.data.length / props.rowsPerPage))
const sortColumn = ref()
const sortOrder = ref("desc")

const sortedData = computed(() => {
  if (!sortColumn.value) {
    return props.data;
  }
  return [...props.data].sort((a, b) => {
    const valueA = a[sortColumn.value];
    const valueB = b[sortColumn.value];

    if (valueA < valueB) return sortOrder.value === 'asc' ? -1 : 1;
    if (valueA > valueB) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.rowsPerPage;
  return sortedData.value.slice(start, start + props.rowsPerPage);
});

const normalizedColumns = computed(() => {
  if (props.columns && props.columns.length > 0) {
    return props.columns.map(column => {
      if (typeof column === 'string') {
        return {
          field: column,
          label: column
        };
      }
      return column;
    });
  }

  if (props.data && props.data.length > 0) {
    const allColumns = Object.keys(props.data[0]);
    const filteredColumns = allColumns.filter(column => !props.excludeColumns.includes(column));

    return filteredColumns.map(column => ({
      field: column,
      label: column
    }));
  }

  return [];
});

const getRowColor = (fonction) => {
  if (fonction) {
    const f = fonction
    switch (true) {
      case f == 'DIRECTION' || f == 'OAD' || f == 'SIC' || f == "MAD": return { "bgc": "var(--sad-nightblue)", "fc": "white" }
      case f.includes("OAG") || f == 'CDS ou CODIS': return { "bgc": "#18163299", "fc": "white" }
      case f == "OFFICIER CODIS" || f == "CDC": return { "bgc": "#18163233", "fc": "var(--sad-nightblue)" }
      default: return { "bgc": "var(--sad-nightblue)", "fc": "white" }
    }
  }
  else {
    return { "bgc": "#dddd", "fc": "var(--sad-nightblue)" }
  }
}

const toggleSort = (field) => {
  if (sortColumn.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = field;
    sortOrder.value = 'asc';
  }
}

const downloadCsv = () => {
  // Assuming tableData.value is an array of objects where the keys are column headers
  const data = props.data
  if (!data || data.length === 0) {
    notifyUser({ icon: "error", message: "Aucune donnée à exporter.", color: "red", position: "bottom", timeout: 2500 })
    return;
  }

  // Extract column headers
  const columns = Object.keys(data[0]);

  // Create CSV string
  const csvRows = [
    columns.join(','), // Header row
    ...data.map(row =>
      columns.map(fieldName => JSON.stringify(row[fieldName], (key, value) =>
        value === null ? '' : value // Handle null values
      )).join(',')
    )
  ];

  const csvString = csvRows.join('\n');
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");

  if (link.download !== undefined) { // Feature check for download attribute
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "export.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

</script>

<style>
.table-container {
  margin: 0.5em;
  overflow-y: auto;
  height: 100%;
  position: relative;
}

table {
  color: var(--sad-nightblue);
  height: 100%;
  width: 100%;
}

th,
td {
  padding: 8px;
  text-align: left;
}

th {
  cursor: pointer;
}


.table-controls {
  position: absolute;
  border-radius: 5px;
  padding: 5px;
  top: 0;
  right: 0;
  width: auto;
  display: flex;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.3s;
}

.table-container:hover .table-controls {
  opacity: 1;
}

.table-scroll {
  overflow-x: auto;
  overflow-y: auto;
  height: 100%;
}



.border-none {
  border-collapse: collapse;
  border: none;
}

.border-none td {
  border: 1px solid white;
}

.border-none tr:first-child td {
  border-top: none;
}

.border-none tr:last-child td {
  border-bottom: none;
}

.border-none tr td:first-child {
  border-left: none;
}

.border-none tr td:last-child {
  border-right: none;
}
</style>
