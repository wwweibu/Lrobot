<template>
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
                <span v-else>{{ groupName }}</span>
                <div class="group-actions">
                  <button @click="startEditGroup('private-'+groupName, groupName)" class="edit-btn">编辑</button>
                  <button @click="deleteGroup('private', groupName)" class="delete-btn">删除</button>
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
                  <span v-else>{{ user }}</span>
                  <div class="user-actions">
                    <button @click="startEditUser('private-'+groupName+'-'+index, user)" class="edit-btn">编辑</button>
                    <button @click="deleteUser('private', groupName, index)" class="delete-btn">删除</button>
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
                <span v-else>{{ groupName }}</span>
                <div class="group-actions">
                  <button @click="startEditGroup('group-'+groupName, groupName)" class="edit-btn">编辑</button>
                  <button @click="deleteGroup('group', groupName)" class="delete-btn">删除</button>
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
                  <span v-else>{{ user }}</span>
                  <div class="user-actions">
                    <button @click="startEditUser('group-'+groupName+'-'+index, user)" class="edit-btn">编辑</button>
                    <button @click="deleteUser('group', groupName, index)" class="delete-btn">删除</button>
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
  
  <script>
  import { ref, onMounted } from 'vue';
  import { http } from '@/api.js';
  
  export default {
    setup() {
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
          privateUsers.value = response.data.private_users || {};
          groupUsers.value = response.data.group_users || {};
          originalData.value = {
            private_users: JSON.parse(JSON.stringify(response.private_users || {})),
            group_users: JSON.parse(JSON.stringify(response.group_users || {}))
          };
        } catch (error) {
          showMessage('加载用户组失败: ' + error.message, true);
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
              showMessage('用户组已存在', true);
              return;
            }
            privateUsers.value[groupName] = [];
          } else {
            if (groupUsers.value[groupName]) {
              showMessage('用户组已存在', true);
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
          showMessage('用户组名称不能为空', true);
          return;
        }
        
        if (type === 'private') {
          if (newName !== originalName && privateUsers.value[newName]) {
            showMessage('用户组名称已存在', true);
            return;
          }
          
          if (newName !== originalName) {
            privateUsers.value[newName] = [...privateUsers.value[originalName]];
            delete privateUsers.value[originalName];
          }
        } else {
          if (newName !== originalName && groupUsers.value[newName]) {
            showMessage('用户组名称已存在', true);
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
          
          await http.put('/users', data);
          originalData.value = {
            private_users: JSON.parse(JSON.stringify(privateUsers.value)),
            group_users: JSON.parse(JSON.stringify(groupUsers.value))
          };
          showMessage('用户组更新成功');
        } catch (error) {
          showMessage('用户组更新失败: ' + error.message, true);
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
  
      return {
        privateUsers,
        groupUsers,
        editingGroup,
        editingUser,
        editingTempName,
        editingTempUser,
        message,
        isError,
        addGroup,
        startEditGroup,
        saveGroupName,
        deleteGroup,
        addUser,
        startEditUser,
        saveUserEdit,
        deleteUser,
        saveChanges,
        discardChanges
      };
    }
  };
  </script>
  
  <style scoped>
  /* 样式部分保持不变，与之前相同 */
  .user-management-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
  }
  
  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
  }
  
  .user-groups-container {
    display: flex;
    gap: 20px;
  }
  
  .user-group {
    flex: 1;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
  
  .edit-btn {
    background-color: #2196f3;
    color: white;
  }
  
  .edit-btn:hover {
    background-color: #0b7dda;
  }
  
  .delete-btn {
    background-color: #f44336;
    color: white;
  }
  
  .delete-btn:hover {
    background-color: #da190b;
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
  </style>