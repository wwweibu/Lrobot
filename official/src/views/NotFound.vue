<template>
    <div class="not-found">
      <h1>Oops! This page doesn't exist.</h1>
      <p>We'll show you a joke to cheer you up!</p>
      <p>{{ joke }}</p>
    </div>
  </template>
  
  <script>
  import {http} from '../api';  // 引入之前的 api.js
  
  export default {
    name: 'NotFound',
    data() {
      return {
        joke: ''  // 存储笑话的变量
      };
    },
    created() {
      this.fetchJoke();
    },
    methods: {
      async fetchJoke() {
        try {
          const response = await http.get('/joke');  // 向 /joke 请求笑话
          this.joke = response.data.joke;  // 假设返回的数据包含笑话
        } catch (error) {
          console.error('Failed to fetch joke:', error);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .not-found {
    text-align: center;
    font-size: 20px;
    padding: 20px;
  }
  </style>