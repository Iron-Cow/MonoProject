import React from 'react';
import './App.css';
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import LoginPage, {action as loginAction} from "./pages/LoginPage";
import AuthenticatedContent from "./pages/AuthenticatedContent";
import Root from "./pages/Root";

const router = createBrowserRouter([
    {
        path: '/',
        element: <Root/>,
        children: [
            {
                path: '/login',
                element: <LoginPage/>,
                action: loginAction,
                errorElement: <div>Login error</div>,
                // children: []
            },
            {
                path: '',
                element: <AuthenticatedContent/>,
                // loader: checkAuthLoader,

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
