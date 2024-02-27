import React from 'react'
import './App.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import LoginPage, { action as loginAction } from './pages/LoginPage'
import { action as logoutAction } from './pages/Logout'
import AuthenticatedContent from './pages/AuthenticatedContent/AuthenticatedContent'
import Root from './pages/Root'
import { checkAuthLoader } from './utils/auth'
import { CardsList } from './pages/CardsList/CardsList'
import { JarDetails } from './pages/JarDetails/JarDetails'
import { JarsList } from './pages/JarsList/JarsList'

const router = createBrowserRouter([
	{
		path: '/',
		element: <Root />,
		children: [
			{
				path: 'login',
				element: <LoginPage />,
				action: loginAction,
				errorElement: (
					<div>
						Login failed, and it is worse, that we all thought :( Please contact
						admin to get some help
					</div>
				)
				// children: []
			},
			{
				path: 'logout',
				loader: logoutAction
			},
			{
				path: '',
				element: <AuthenticatedContent />,
				loader: checkAuthLoader,
				id: 'token',
				// errorElement: <ErrorPage />,
				children: [
					{
						path: 'cards',
						element: <CardsList />
					},
					{
						path: 'jars',
						element: <JarsList />
					}
				]
			}
		]
	}
])

function App() {
	return <RouterProvider router={router} />
}

export default App
