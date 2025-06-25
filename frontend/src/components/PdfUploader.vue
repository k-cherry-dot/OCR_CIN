<template>
  <div class="mb-4">
    <label
      for="pdf-upload"
      class="inline-block bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded cursor-pointer"
    >
      Upload PDF
    </label>
    <input
      id="pdf-upload"
      type="file"
      @change="onFileChange"
      accept="application/pdf"
      class="hidden"
    />
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['uploadId'],
  emits: ['uploaded'],
  methods: {
    onFileChange(e) {
      const file = e.target.files[0];
      const form = new FormData();
      form.append('upload_id', this.uploadId);
      form.append('file', file);
      axios
        .post('/api/uploads/pdf', form)
        .then(res => this.$emit('uploaded', res.data.result_id));
    }
  }
};
</script>
