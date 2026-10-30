<template>
  <div style="padding: 20px; font-family: sans-serif; max-width: 1200px; margin: auto;">
    
    <!-- ЭКРАН 1: ЛОГИН -->
    <div v-if="!token" style="max-width: 300px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px;">
      <h2>Вход в систему</h2>
      <input v-model="username" placeholder="Логин (admin)" style="width: 100%; padding: 8px; margin-bottom: 10px;" />
      <input v-model="password" type="password" placeholder="Пароль (admin12345)" style="width: 100%; padding: 8px; margin-bottom: 10px;" />
      <button @click="login" style="width: 100%; padding: 10px; background-color: #42b983; color: white; border: none; cursor: pointer;">Войти</button>
      <p v-if="error" style="color: red;">{{ error }}</p>
    </div>

    <!-- ЭКРАН 2: ДАШБОРД -->
    <div v-else>
      <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px;">
        <h2>Панель управления сервисом</h2>
        <button @click="logout" style="padding: 5px 15px; cursor: pointer;">Выйти</button>
      </div>

      <!-- Блок запуска -->
      <div style="border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 8px; background: #f9f9f9; display: flex; align-items: center; gap: 20px;">
        <div>
          <label>Год: 
            <select v-model="selectedYear" style="padding: 5px; font-size: 16px;">
              <option value="2025">2025</option>
              <option value="2026">2026</option>
              <option value="2027">2027</option>
            </select>
          </label>
        </div>
        <div>
          <label>Месяц: 
            <select v-model="selectedMonth" style="padding: 5px; font-size: 16px;">
              <option v-for="(name, index) in months" :key="index" :value="index + 1">{{ name }}</option>
            </select>
          </label>
        </div>
        <button @click="startRun" :disabled="loading" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; font-size: 16px;">
          {{ loading ? 'Идет подсчет...' : 'Запустить расчет' }}
        </button>
        <span v-if="runResult" style="color: green; font-weight: bold;">{{ runResult }}</span>
      </div>

      <div style="display: flex; gap: 20px;">
        <!-- Левая колонка: История запусков -->
        <div style="flex: 1; border: 1px solid #ccc; padding: 15px; border-radius: 8px;">
          <h3>История запусков</h3>
          <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;">
            <tr style="background: #f0f0f0;">
              <th style="padding: 8px;">ID</th>
              <th style="padding: 8px;">Период</th>
              <th style="padding: 8px;">Действие</th>
            </tr>
            <tr v-for="run in runs" :key="run.id">
              <td style="padding: 8px;">{{ run.id }}</td>
              <td style="padding: 8px;">{{ run.period_year }}-{{ run.period_month }}</td>
              <td style="padding: 8px;">
                <button @click="loadResults(run.id)" style="cursor: pointer;">Посмотреть</button>
              </td>
            </tr>
          </table>
        </div>

        <!-- Правая колонка: Результаты (по клиентам) -->
        <div style="flex: 2; border: 1px solid #ccc; padding: 15px; border-radius: 8px; background: #fafafa;">
          <h3 v-if="currentRunId">Результаты расчета (Запуск #{{ currentRunId }})</h3>
          <p v-else>Нажмите "Посмотреть" в истории слева, чтобы загрузить результаты.</p>
          
          <div v-if="groupedSuggestions.length > 0">
            <div v-for="group in groupedSuggestions" :key="group.client_id" style="border: 1px solid #ddd; margin-bottom: 15px; padding: 10px; border-radius: 5px; background: white;">
              <h4>Клиент ID: {{ clients[group.client_id] || group.client_id }}</h4>
              
              <table border="1" style="width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px;">
                <tr style="background: #eee;">
                  <th style="padding: 6px;">Работа</th>
                  <th style="padding: 6px;">Часы</th>
                  <th style="padding: 6px;">Статус</th>
                  <th style="padding: 6px;">Действия</th>
                </tr>
                <tr v-for="s in group.items" :key="s.id">
                  <td style="padding: 6px;">
                    {{ s.title }} 
                    <span v-if="s.source === 'LLM'" style="color: purple; font-size: 11px; font-weight: bold;">[AI]</span>
                  </td>
                  <td style="padding: 6px;">{{ s.estimated_hours }} ч</td>
                  <td style="padding: 6px;">
                    <span :style="{color: s.status === 'CREATED' ? 'blue' : (s.status === 'APPROVED' ? 'green' : (s.status === 'REJECTED' ? 'red' : 'orange'))}">
                      {{ translateStatus(s.status) }}
                    </span>
                  </td>
                  <td style="padding: 6px;">
                    <button v-if="s.status === 'NEW'" @click="approve(s.id)" style="cursor: pointer; background: #d4edda; margin-right: 5px;">Одобрить</button>
                    <button v-if="s.status === 'NEW'" @click="reject(s.id)" style="cursor: pointer; background: #f8d7da; margin-right: 5px;">Отклонить</button>
                    <button v-if="s.status === 'APPROVED'" @click="createTask(s.id)" style="cursor: pointer; background: #cce5ff;">Создать в Redmine</button>
                  </td>
                </tr>
              </table>
            </div>
          </div>
          <p v-else-if="currentRunId && groupedSuggestions.length === 0">В этом запуске предложений не найдено.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from './api';

const token = ref(localStorage.getItem('token'));
const username = ref('');
const password = ref('');
const error = ref('');
const runs = ref([]);
const loading = ref(false);
const runResult = ref('');
const currentRunId = ref(null);
const suggestions = ref([]);


const clients = ref({}); // Словарь для быстрого поиска имени по ID

const fetchClients = async () => {
  const res = await api.get('/api/runs/clients');
  const map = {};
  res.data.forEach(c => { map[c.id] = c.name; });
  clients.value = map;
};

onMounted(() => {
  if (token.value) {
    fetchRuns();
    fetchClients(); // загрузка клиентов
  }
});


// Выбор периода
const selectedYear = ref(2026);
const selectedMonth = ref(10);
const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

// Вычисляемое свойство: группируем предложения по клиентам
const groupedSuggestions = computed(() => {
  const groups = {};
  for (const s of suggestions.value) {
    if (!groups[s.client_id]) {
      groups[s.client_id] = { client_id: s.client_id, items: [] };
    }
    groups[s.client_id].items.push(s);
  }
  return Object.values(groups);
});

// перевод статусов на русский
const translateStatus = (status) => {
  const map = {
    'NEW': 'Новое',
    'APPROVED': 'Одобрено',
    'REJECTED': 'Отклонено',
    'CREATED': 'Задача создана'
  };
  return map[status] || status;
};

const login = async () => {
  try {
    error.value = '';
    const formData = new URLSearchParams();
    formData.append('username', username.value);
    formData.append('password', password.value);
    const res = await api.post('/auth/login', formData, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
    localStorage.setItem('token', res.data.access_token);
    token.value = res.data.access_token;
    fetchRuns();
  } catch (e) {
    error.value = 'Неверный логин или пароль';
  }
};

const logout = () => {
  localStorage.removeItem('token');
  token.value = null;
  runs.value = [];
  suggestions.value = [];
  currentRunId.value = null;
};

const fetchRuns = async () => {
  const res = await api.get('/api/runs');
  runs.value = res.data;
};

const startRun = async () => {
  loading.value = true;
  runResult.value = '';
  try {
    const res = await api.post('/api/runs', { 
      period_year: parseInt(selectedYear.value), 
      period_month: parseInt(selectedMonth.value) 
    });
    runResult.value = `Успех! Создано предложений: ${res.data.suggestions_created}`;
    fetchRuns();
  } catch (e) {
    runResult.value = 'Ошибка при запуске';
  } finally {
    loading.value = false;
  }
};

const loadResults = async (runId) => {
  currentRunId.value = runId;
  const res = await api.get(`/api/suggestions?run_id=${runId}`);
  suggestions.value = res.data;
};

const approve = async (id) => {
  await api.post(`/api/suggestions/${id}/approve`);
  loadResults(currentRunId.value);
};

const reject = async (id) => {
  await api.post(`/api/suggestions/${id}/reject`);
  loadResults(currentRunId.value);
};

const createTask = async (id) => {
  await api.post(`/api/suggestions/${id}/create-task`);
  loadResults(currentRunId.value);
};

onMounted(() => {
  if (token.value) fetchRuns();
});
</script>