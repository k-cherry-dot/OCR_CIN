<template>
  <div class="overflow-auto bg-white shadow rounded-lg p-4">
    <h2 class="text-xl font-semibold mb-4">Results</h2>
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Field
          </th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Value
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-for="(val, key) in results" :key="key">
          <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-700">{{ key }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ val }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import axios from 'axios';

export default {
  props: ['uploadId'],
  setup(props) {
    const results = ref({});

    onMounted(() => {
      axios
        .get(`/api/results/${props.uploadId}`)
        .then(res => {
          results.value = res.data;
        });
    });

    return { results };
  }
};
</script>
