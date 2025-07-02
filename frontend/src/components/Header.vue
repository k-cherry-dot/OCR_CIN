<template>
  <header class="header">
    <!-- Try using the @ path and adjust based on the results -->
    <img :src="logoSrc" alt="Ecole Centrale Casablanca" class="logo" />
    <h2 class="title">OCR_CIN</h2>
    <nav>
      <router-link to="/" class="nav-link">Upload</router-link>
      <router-link to="/results" class="nav-link">Results</router-link>
    </nav>
  </header>
</template>

<script setup>
const logoSrc = new URL('@/assets/logo-ecc.png', import.meta.url).href
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #fff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.logo {
  height: 40px;
}

.title {
  font-size: 24px;
  font-weight: bold;
}

.nav-link {
  padding: 8px;
  text-decoration: none;
  color: #007BFF;
}

.nav-link:hover {
  text-decoration: underline;
}
</style>
