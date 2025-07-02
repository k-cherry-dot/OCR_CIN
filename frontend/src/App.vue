<template>
  <div class="flex flex-col min-h-screen">
    <Header />

    <main class="flex-1 bg-gray-50">
      <router-view/>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
</script>
