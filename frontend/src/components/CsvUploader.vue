<template>
  <div class="bg-white shadow-md rounded-lg p-4">
    <label class="block text-sm font-semibold text-gray-700 mb-2">CSV File</label>
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      @change="onFileChange"
      accept=".csv"
    />
    <button
      @click="$refs.fileInput.click()"
      class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
    >
      Select CSV File
    </button>
    <span v-if="fileName" class="ml-3 text-gray-600">{{ fileName }}</span>
  </div>
</template>

<script>
import axios from 'axios';
import { ref } from 'vue';

export default {
  emits: ['uploaded'],
  setup(props, { emit }) {
    const fileName = ref('');

    function onFileChange(e) {
      const file = e.target.files[0];
      if (!file) return;
      fileName.value = file.name;

      const form = new FormData();
      form.append('file', file);
      axios
        .post('/api/uploads/csv', form)
        .then(res => emit('uploaded', res.data.upload_id))
        .catch(() => {
          fileName.value = '';
          alert('Failed to upload CSV');
        });
    }

    return { fileName, onFileChange };
  }
};
</script>
