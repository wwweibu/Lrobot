class<template>
  <Sidebar :githubLink="'http://wwweibu.github.io/Lrobot/docs/1项目总览/3项目功能#用户页'"/>
  <div class="user-management-container">
    <h1>用户组管理</h1>

    <div class="user-groups-container">
      <!-- 私聊用户组 -->
      <div class="user-group private-group">
        <h2>私聊用户组</h2>
        <div class="group-actions">
          <button @click="addGroup('private')" class="add-group-btn">新增用户组</button>
        </div>
        <div class="groups-list">
          <div v-for="(users, groupName) in privateUsers" :key="'private-'+groupName" class="group-item">
            <div class="group-header">
              <input
                v-if="editingGroup === 'private-'+groupName"
                :value="editingTempName"
                @input="editingTempName = $event.target.value"
                @blur="saveGroupName('private', editingTempName, editingOriginalName)"
                @keyup.enter="saveGroupName('private', editingTempName, editingOriginalName)"
              />
              <span v-else @click="startEditGroup('private-'+groupName, groupName)" class="click-edit">{{ groupName }}</span>
              <div class="group-actions">
                <button @click="deleteGroup('private', groupName)" class="delete-btn" title="删除">
                  <svg t="1757768742307" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5680" width="18" height="18"><path d="M358.925672 596.814688v30.450522c0 17.248849 13.985526 31.233352 31.233352 31.233352 17.248849 0 31.233352-13.985526 31.233352-31.233352v-30.450522c0-17.248849-13.985526-31.233352-31.233352-31.233352-17.248849 0-31.233352 13.985526-31.233352 31.233352zM602.506317 596.814688v30.450522c0 17.248849 13.985526 31.233352 31.233352 31.233352s31.233352-13.985526 31.233351-31.233352v-30.450522c0-17.248849-13.984503-31.233352-31.233351-31.233352s-31.233352 13.985526-31.233352 31.233352zM437.047937 699.686636c-14.650675 9.104355-19.155269 28.360931-10.04989 43.01263 11.015891 17.73185 41.238216 47.740304 84.651982 47.740304 43.195801 0 73.79368-29.780257 85.059258-47.379077 9.216919-14.391778 5.03262-33.338293-9.237385-42.742477-14.270005-9.393951-33.576723-5.409197-43.159985 8.739035-0.12689 0.188288-13.049201 18.915815-32.661888 18.915815-19.028379 0-30.93864-17.274432-31.772634-18.530028-9.175987-14.412244-28.259624-18.788925-42.829458-9.756202zM907.576407 160.082952H699.352015v-26.882254c0-40.145325-32.692586-72.807213-72.878844-72.807213h-229.046626c-40.186258 0-72.878844 32.661887-72.878844 72.807213v26.882254H116.323309c-17.248849 0-31.233352 13.984503-31.233352 31.233352s13.984503 31.233352 31.233352 31.233351h791.253098c17.248849 0 31.233352-13.984503 31.233352-31.233351s-13.985526-31.233352-31.233352-31.233352z m-270.692119 0H387.014404v-26.882254c0-5.607718 4.768607-10.340509 10.411117-10.340509h229.046627c5.64251 0 10.411117 4.732791 10.411117 10.340509v26.882254z" fill="#999999" p-id="5681"></path><path d="M824.286446 259.279185c-17.248849 0-31.233352 13.984503-31.233352 31.233352v530.07261c0 40.089044-32.692586 72.705905-72.878844 72.705906H303.725466c-40.186258 0-72.878844-32.616862-72.878844-72.705906v-530.07261c0-17.248849-13.984503-31.233352-31.233352-31.233352s-31.233352 13.984503-31.233352 31.233352v530.07261c0 74.535577 60.71378 135.172609 135.345548 135.172609h416.448784c74.632791 0 135.345548-60.637032 135.345548-135.172609v-530.07261c0-17.248849-13.984503-31.233352-31.233352-31.233352z" fill="#999999" p-id="5682"></path><path d="M355.781052 259.279185c-17.248849 0-31.233352 13.984503-31.233351 31.233352v167.494758c0 17.248849 13.985526 31.233352 31.233351 31.233352 17.248849 0 31.233352-13.985526 31.233352-31.233352v-167.494758c0-17.248849-13.984503-31.233352-31.233352-31.233352zM699.352015 458.007295v-167.494758c0-17.248849-13.984503-31.233352-31.233351-31.233352s-31.233352 13.984503-31.233352 31.233352v167.494758c0 17.248849 13.985526 31.233352 31.233352 31.233352s31.233352-13.984503 31.233351-31.233352zM511.949858 489.240647c17.248849 0 31.233352-13.985526 31.233352-31.233352v-167.494758c0-17.248849-13.985526-31.233352-31.233352-31.233352s-31.233352 13.984503-31.233352 31.233352v167.494758c-0.001023 17.248849 13.984503 31.233352 31.233352 31.233352z" fill="#999999" p-id="5683"></path></svg>
                </button>
              </div>
            </div>
            <div class="users-list">
              <div v-for="(user, index) in users" :key="index" class="user-item">
                <input
                  v-if="editingUser === 'private-'+groupName+'-'+index"
                  :value="editingTempUser"
                  @input="editingTempUser = $event.target.value"
                  @blur="saveUserEdit('private', groupName, index)"
                  @keyup.enter="saveUserEdit('private', groupName, index)"
                />
                <span v-else @click="startEditUser('private-'+groupName+'-'+index, user)" class="click-edit">{{ user }}</span>
                <div class="user-actions">
                  <button @click="deleteUser('private', groupName, index)" class="delete-btn" title="删除">
                    <svg t="1757768742307" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5680" width="18" height="18"><path d="M358.925672 596.814688v30.450522c0 17.248849 13.985526 31.233352 31.233352 31.233352 17.248849 0 31.233352-13.985526 31.233352-31.233352v-30.450522c0-17.248849-13.985526-31.233352-31.233352-31.233352-17.248849 0-31.233352 13.985526-31.233352 31.233352zM602.506317 596.814688v30.450522c0 17.248849 13.985526 31.233352 31.233352 31.233352s31.233352-13.985526 31.233351-31.233352v-30.450522c0-17.248849-13.984503-31.233352-31.233351-31.233352s-31.233352 13.985526-31.233352 31.233352zM437.047937 699.686636c-14.650675 9.104355-19.155269 28.360931-10.04989 43.01263 11.015891 17.73185 41.238216 47.740304 84.651982 47.740304 43.195801 0 73.79368-29.780257 85.059258-47.379077 9.216919-14.391778 5.03262-33.338293-9.237385-42.742477-14.270005-9.393951-33.576723-5.409197-43.159985 8.739035-0.12689 0.188288-13.049201 18.915815-32.661888 18.915815-19.028379 0-30.93864-17.274432-31.772634-18.530028-9.175987-14.412244-28.259624-18.788925-42.829458-9.756202zM907.576407 160.082952H699.352015v-26.882254c0-40.145325-32.692586-72.807213-72.878844-72.807213h-229.046626c-40.186258 0-72.878844 32.661887-72.878844 72.807213v26.882254H116.323309c-17.248849 0-31.233352 13.984503-31.233352 31.233352s13.984503 31.233352 31.233352 31.233351h791.253098c17.248849 0 31.233352-13.984503 31.233352-31.233351s-13.985526-31.233352-31.233352-31.233352z m-270.692119 0H387.014404v-26.882254c0-5.607718 4.768607-10.340509 10.411117-10.340509h229.046627c5.64251 0 10.411117 4.732791 10.411117 10.340509v26.882254z" fill="#999999" p-id="5681"></path><path d="M824.286446 259.279185c-17.248849 0-31.233352 13.984503-31.233352 31.233352v530.07261c0 40.089044-32.692586 72.705905-72.878844 72.705906H303.725466c-40.186258 0-72.878844-32.616862-72.878844-72.705906v-530.07261c0-17.248849-13.984503-31.233352-31.233352-31.233352s-31.233352 13.984503-31.233352 31.233352v530.07261c0 74.535577 60.71378 135.172609 135.345548 135.172609h416.448784c74.632791 0 135.345548-60.637032 135.345548-135.172609v-530.07261c0-17.248849-13.984503-31.233352-31.233352-31.233352z" fill="#999999" p-id="5682"></path><path d="M355.781052 259.279185c-17.248849 0-31.233352 13.984503-31.233351 31.233352v167.494758c0 17.248849 13.985526 31.233352 31.233351 31.233352 17.248849 0 31.233352-13.985526 31.233352-31.233352v-167.494758c0-17.248849-13.984503-31.233352-31.233352-31.233352zM699.352015 458.007295v-167.494758c0-17.248849-13.984503-31.233352-31.233351-31.233352s-31.233352 13.984503-31.233352 31.233352v167.494758c0 17.248849 13.985526 31.233352 31.233352 31.233352s31.233352-13.984503 31.233351-31.233352zM511.949858 489.240647c17.248849 0 31.233352-13.985526 31.233352-31.233352v-167.494758c0-17.248849-13.985526-31.233352-31.233352-31.233352s-31.233352 13.984503-31.233352 31.233352v167.494758c-0.001023 17.248849 13.984503 31.233352 31.233352 31.233352z" fill="#999999" p-id="5683"></path></svg>
                  </button>
                </div>
              </div>
              <button @click="addUser('private', groupName)" class="add-user-btn">添加用户</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 群聊用户组 -->
      <div class="user-group group-chat">
        <h2>群聊用户组</h2>
        <div class="group-actions">
          <button @click="addGroup('group')" class="add-group-btn">新增用户组</button>
        </div>
        <div class="groups-list">
          <div v-for="(users, groupName) in groupUsers" :key="'group-'+groupName" class="group-item">
            <div class="group-header">
              <input
                v-if="editingGroup === 'group-'+groupName"
                :value="editingTempName"
                @input="editingTempName = $event.target.value"
                @blur="saveGroupName('group', editingTempName, editingOriginalName)"
                @keyup.enter="saveGroupName('group', editingTempName, editingOriginalName)"
              />
              <span v-else @click="startEditGroup('group-'+groupName, groupName)" class="click-edit">{{ groupName }}</span>
              <div class="group-actions">
                <button @click="deleteGroup('group', groupName)" class="delete-btn" title="删除">
                  🗑️
                </button>
              </div>
            </div>
            <div class="users-list">
              <div v-for="(user, index) in users" :key="index" class="user-item">
                <input
                  v-if="editingUser === 'group-'+groupName+'-'+index"
                  :value="editingTempUser"
                  @input="editingTempUser = $event.target.value"
                  @blur="saveUserEdit('group', groupName, index)"
                  @keyup.enter="saveUserEdit('group', groupName, index)"
                />
                <span v-else @click="startEditUser('group-'+groupName+'-'+index, user)" class="click-edit">{{ user }}</span>
                <div class="user-actions">
                  <button @click="deleteUser('group', groupName, index)" class="delete-btn" title="删除">
                    🗑️
                  </button>
                </div>
              </div>
              <button @click="addUser('group', groupName)" class="add-user-btn">添加用户</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="save-actions">
      <button @click="saveChanges" class="save-btn">保存更改</button>
      <button @click="discardChanges" class="discard-btn">放弃更改</button>
    </div>

    <div v-if="message" class="message" :class="{ error: isError }">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { http } from '@/api.js';
import Sidebar from './Sidebar.vue';

const privateUsers = ref({});
const groupUsers = ref({});
const originalData = ref({});
const editingGroup = ref(null);
const editingUser = ref(null);
const editingTempName = ref('');
const editingTempUser = ref('');
const editingOriginalName = ref('');
const message = ref('');
const isError = ref(false);

// 加载用户组数据
const loadUserGroups = async () => {
  try {
    const response = await http.get('/users');
    if (response.data.status === "success") {
      privateUsers.value = response.data.data.private_users || {};
      groupUsers.value = response.data.data.group_users || {};
      originalData.value = {
        private_users: JSON.parse(JSON.stringify(privateUsers.value || {})),
        group_users: JSON.parse(JSON.stringify(groupUsers.value || {}))
      };
    } else {
      alert('用户组加载失败:' + (response.data.data || '网络异常，请稍后重试'));
    }
  } catch (error) {
    alert('用户组加载失败: ' + (error.message || '网络异常，请稍后重试'));
  }
};

// 显示消息
const showMessage = (msg, error = false) => {
  message.value = msg;
  isError.value = error;
  setTimeout(() => {
    message.value = '';
    isError.value = false;
  }, 3000);
};

// 添加用户组
const addGroup = (type) => {
  const groupName = prompt('请输入新用户组名称:');
  if (groupName) {
    if (type === 'private') {
      if (privateUsers.value[groupName]) {
        alert('用户组已存在');
        return;
      }
      privateUsers.value[groupName] = [];
    } else {
      if (groupUsers.value[groupName]) {
        alert('用户组已存在');
        return;
      }
      groupUsers.value[groupName] = [];
    }
  }
};

// 开始编辑用户组名称
const startEditGroup = (groupId, currentName) => {
  editingGroup.value = groupId;
  editingOriginalName.value = currentName;
  editingTempName.value = currentName;
};

// 保存用户组名称更改
const saveGroupName = (type, newName, originalName) => {
  if (!newName.trim()) {
    alert('用户组名称不能为空');
    return;
  }

  if (type === 'private') {
    if (newName !== originalName && privateUsers.value[newName]) {
      alert('用户组名称已存在');
      return;
    }

    if (newName !== originalName) {
      privateUsers.value[newName] = [...privateUsers.value[originalName]];
      delete privateUsers.value[originalName];
    }
  } else {
    if (newName !== originalName && groupUsers.value[newName]) {
      alert('用户组名称已存在');
      return;
    }

    if (newName !== originalName) {
      groupUsers.value[newName] = [...groupUsers.value[originalName]];
      delete groupUsers.value[originalName];
    }
  }

  editingGroup.value = null;
  editingOriginalName.value = '';
  editingTempName.value = '';
};

// 删除用户组
const deleteGroup = (type, groupName) => {
  if (confirm(`确定要删除用户组 "${groupName}" 吗?`)) {
    if (type === 'private') {
      delete privateUsers.value[groupName];
    } else {
      delete groupUsers.value[groupName];
    }
  }
};

// 添加用户
const addUser = (type, groupName) => {
  const user = prompt('请输入新用户ID:');
  if (user) {
    if (type === 'private') {
      privateUsers.value[groupName].push(user);
    } else {
      groupUsers.value[groupName].push(user);
    }
  }
};

// 开始编辑用户
const startEditUser = (userId, currentValue) => {
  editingUser.value = userId;
  editingTempUser.value = currentValue;
};

// 保存用户编辑
const saveUserEdit = (type, groupName, index) => {
  if (type === 'private') {
    privateUsers.value[groupName][index] = editingTempUser.value;
  } else {
    groupUsers.value[groupName][index] = editingTempUser.value;
  }
  editingUser.value = null;
  editingTempUser.value = '';
};

// 删除用户
const deleteUser = (type, groupName, index) => {
  if (confirm('确定要删除该用户吗?')) {
    if (type === 'private') {
      privateUsers.value[groupName].splice(index, 1);
    } else {
      groupUsers.value[groupName].splice(index, 1);
    }
  }
};

// 保存更改
const saveChanges = async () => {
  try {
    const data = {
      private_users: privateUsers.value,
      group_users: groupUsers.value
    };

    const res = await http.put('/users', data);
    if (res.data.status === "success") {
      originalData.value = {
        private_users: JSON.parse(JSON.stringify(privateUsers.value)),
        group_users: JSON.parse(JSON.stringify(groupUsers.value))
      };
      alert('用户组更新成功');
    } else {
      alert('用户组更新失败:' + (res.data.data || '网络异常，请稍后重试'));
    }
  } catch (error) {
    alert('用户组更新失败: ' + (error.message || '网络异常，请稍后重试'));
  }
};

// 放弃更改
const discardChanges = () => {
  if (confirm('确定要放弃所有更改吗?')) {
    privateUsers.value = JSON.parse(JSON.stringify(originalData.value.private_users));
    groupUsers.value = JSON.parse(JSON.stringify(originalData.value.group_users));
  }
};

onMounted(() => {
  loadUserGroups();
});
</script>

<style scoped>
.user-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  height: 100vh;
  overflow-y: auto;
  box-sizing: border-box;
  background: #fafafa;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.user-groups-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.user-group {
  flex: 1 1 45%;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  min-width: 300px;
  box-sizing: border-box;
}

.private-group {
  background-color: #f0f8ff;
  border: 1px solid #add8e6;
}

.group-chat {
  background-color: #fff0f5;
  border: 1px solid #ffb6c1;
}

h2 {
  margin-top: 0;
  color: #555;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.group-actions {
  margin-bottom: 15px;
}

button {
  padding: 5px 10px;
  margin-right: 5px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.add-group-btn {
  background-color: #4caf50;
  color: white;
}

.add-group-btn:hover {
  background-color: #45a049;
}

.delete-btn {
  background-color: transparent;
  color: #f44336;
  font-size: 16px;
  padding: 2px 6px;
}

.delete-btn:hover {
  background-color: #ffebee;
}

.add-user-btn {
  background-color: #ff9800;
  color: white;
  margin-top: 10px;
}

.add-user-btn:hover {
  background-color: #e68a00;
}

.group-item {
  margin-bottom: 20px;
  padding: 10px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px dashed #eee;
}

.group-header input {
  flex-grow: 1;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.users-list {
  padding-left: 15px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px dotted #eee;
}

.user-item:last-child {
  border-bottom: none;
}

.user-item input {
  flex-grow: 1;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
}

.user-actions {
  display: flex;
  gap: 5px;
}

.save-actions {
  margin-top: 30px;
  text-align: center;
}

.save-btn {
  background-color: #4caf50;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
}

.save-btn:hover {
  background-color: #45a049;
}

.discard-btn {
  background-color: #9e9e9e;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
  margin-left: 15px;
}

.discard-btn:hover {
  background-color: #757575;
}

.message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
}

.message.error {
  background-color: #ffebee;
  color: #f44336;
  border: 1px solid #f44336;
}

.message:not(.error) {
  background-color: #e8f5e9;
  color: #4caf50;
  border: 1px solid #4caf50;
}

.click-edit {
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.click-edit:hover {
  background-color: #e0e0e0;
}

@media (max-width: 768px) {
  .user-groups-container {
    flex-direction: column;
  }

  .user-group {
    flex: 1 1 100%;
  }
}
</style>