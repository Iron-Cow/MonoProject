import React from 'react';
import './App.css';
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import LoginPage, {action as loginAction} from "./pages/LoginPage";
import {action as logoutAction} from "./pages/Logout";
import AuthenticatedContent from "./pages/AuthenticatedContent";
import Root from "./pages/Root";
import {checkAuthLoader} from "./utils/auth";

const router = createBrowserRouter([
    {
        path: '/',
        element: <Root/>,
        children: [
            {
                path: '/login',
                element: <LoginPage/>,
                action: loginAction,
                errorElement: <div>Login failed, and it is worse, that we all thought :( Please contact admin to get
                    some help</div>,
                // children: []
            },
            {
                path: 'logout',
                loader: logoutAction,
            },
            {
                path: '',
                element: <AuthenticatedContent/>,
                loader: checkAuthLoader,


                // errorElement: <ErrorPage />,
                // children: []
            },
        ]
    },

])

function App() {
    return <RouterProvider router={router}/>;
}

export default App;
