<template>
  <div class="mb-4">
    <label class="block mb-2">Upload CSV:</label>
    <input type="file" @change="onFileChange" accept=".csv" class="border p-2" />
  </div>
</template>

<script>
import axios from 'axios';
export default {
  emits: ['uploaded'],
methods: {
  onFileChange(e) {
    const file = e.target.files[0];
    console.log('Selected file:', file);  // Log the file to see if it's being selected
    const form = new FormData();
    form.append('file', file);
    axios.post('/api/uploads/csv', form)
      .then(res => {
        console.log('Upload successful:', res.data); // Log the response from the server
        this.$emit('uploaded', res.data.upload_id);
      })
      .catch(error => {
        console.error('Error uploading file:', error); // Log any errors
      });
  }
}

</script>
