// 配置路由
import Vue from 'vue';
import VueRouter from 'vue-router';
import ChartView from '@/components/ChartView'
import Home from '@/pages/Home'

Vue.use(VueRouter);

export default new VueRouter({
    mode: "history",
    routes: [
        {
            path: '/',
            redirect: '/home'
        },
        {
            path: '/home',
            name: 'Home',
            component: Home
        },
        {
            path: '/chart',
            name: 'Chart',
            component: ChartView
        },
        {
            path: "*",
            redirect: "/home"
        }
    ]
})