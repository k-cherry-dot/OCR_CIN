<template>
  <div>
    <h2 class="text-xl font-semibold mb-2">Results</h2>
    <table class="min-w-full table-auto mb-4">
      <thead>
        <tr>
          <th>Field</th><th>Extracted</th><th>Expected</th><th>Match?</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(val, key) in tableData" :key="key">
          <td>{{ key }}</td>
          <td>{{ val.extracted }}</td>
          <td>{{ val.expected }}</td>
          <td>{{ val.match }}</td>
        </tr>
      </tbody>
    </table>
    <button v-if="excelUrl" @click="downloadExcel" class="px-4 py-2">Download Excel</button>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, watchEffect } from 'vue';

export default {
  props: ['uploadId'],
  setup(props) {
    const tableData = ref({});
    const excelUrl = ref('');

    watchEffect(() => {
      if (!props.uploadId) return;
      axios.get(`/api/results/${props.uploadId}`)
        .then(res => {
          const d = res.data.data;
          tableData.value = {
            card_number:   { extracted: d.extracted.card_number,   expected: d.expected.card_number,   match: d.matches.card_number },
            surname:       { extracted: d.extracted.surname,       expected: d.expected.surname,       match: d.matches.surname },
            given_names:   { extracted: d.extracted.given_names,   expected: d.expected.given_names,   match: d.matches.given_names },
            date_of_birth: { extracted: d.extracted.date_of_birth, expected: d.expected.date_of_birth, match: d.matches.date_of_birth },
            gender:        { extracted: d.extracted.gender,        expected: d.expected.gender,        match: d.matches.gender }
          };
          excelUrl.value = res.data.excel_url;
        });
    });

    function downloadExcel() {
      window.location = excelUrl.value;
    }

    return { tableData, excelUrl, downloadExcel };
  }
};
</script>
