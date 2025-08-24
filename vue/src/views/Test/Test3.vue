<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Layout3 测试页面</h2>

    <!-- 测试容器 -->
    <div class="layout3-container border rounded shadow bg-white" style="height: 500px;">
      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>邮箱</th>
            <th>地址</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>张三</td>
            <td>zhangsan@example.com</td>
            <td>北京市朝阳区某某街道100号超级长的详细地址测试是否会自动换行显示</td>
            <td>这是一个很长的备注字段，用来测试表格在 PC 端和手机端卡片模式下的换行情况。</td>
          </tr>
          <tr>
            <td>李四</td>
            <td>lisi_very_long_email_address_test@example.com</td>
            <td>上海市浦东新区世纪大道2000号办公大厦顶楼8888室，这里文字特别长特别长特别长</td>
            <td>手机端应当展示为卡片模式，每个字段：值单独换行。</td>
          </tr>
          <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
                    <tr>
            <td>王五</td>
            <td>wuwu@example.com</td>
            <td>广州市天河区长长长长长长的地址测试用例</td>
            <td>PC 端应该是表格模式，表头固定在上方。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: "Test5",
  mounted() {
    // 监听 layout3-dragend 事件
    const wrapper = this.$el.querySelector('.layout3-container')
    if (wrapper) {
      wrapper.addEventListener('layout3-dragend', e => {
        console.log('收到拖拽事件:', e.detail)
      })
    }
  }
}
</script>

<style>
/* 让长内容自动换行 */
.layout3-container td,
.layout3-container th,
.layout3-card,
.layout3-field {
  word-break: break-word;
  white-space: normal;
}
</style>
