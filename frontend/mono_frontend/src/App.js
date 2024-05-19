import React from 'react'
import './App.css'
import {createBrowserRouter, RouterProvider} from 'react-router-dom'
import LoginPage, {action as loginAction} from './pages/LoginPage'
import {action as logoutAction} from './pages/Logout'
import AuthenticatedContent from './pages/AuthenticatedContent/AuthenticatedContent'
import Root from './pages/Root'
import {checkAuthLoader} from './utils/auth'
import {CardsList, getCards} from './pages/CardsList/CardsList'
import {getJars, JarsList} from './pages/JarsList/JarsList'
import {JarDetails, jarDetailsLoader} from './pages/JarDetails/JarDetails'

const router = createBrowserRouter([
    {
        path: '/',
        element: <Root/>,
        children: [
            {
                path: 'login',
                element: <LoginPage/>,
                action: loginAction,
                errorElement: (
                    <div>
                        Login failed, and it is worse, that we all thought :( Please contact
                        admin to get some help
                    </div>
                )
            },
            {
                path: 'logout',
                loader: logoutAction
            },
            {
                path: '',
                element: <AuthenticatedContent/>,
                loader: checkAuthLoader,
                id: 'token',
                children: [
                    {
                        path: 'cards',
                        element: <CardsList/>,
                        id: 'cards',
                        loader: getCards
                    },
                    {
                        path: 'jars',
                        element: <JarsList/>,
                        id: 'jars',
                        loader: getJars
                    },
                    {
                        path: '/jars/:jarId/',
                        element: <JarDetails/>,
                        id: 'jar',
                        loader: jarDetailsLoader
                    }
                ]
            }
        ]
    }
])

function App() {
    return <RouterProvider router={router}/>
}

export default App
