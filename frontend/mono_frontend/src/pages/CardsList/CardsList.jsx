import { useEffect, useState } from 'react'
import { BACKEND_URL } from '../../config/envs'
import './CardsList.css'
import { CardItem } from '../../components/CardItem'
import { useRouteLoaderData } from 'react-router-dom'

export const getCards = async function (token) {
	const endpoint = `${BACKEND_URL}/monobank/monocards`

	const response = await fetch(endpoint, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
	const data = await response.json()

	if (!response.ok) {
		return null
	}
	return data
}

export const CardsList = () => {
	const token = useRouteLoaderData('token')
	const [cardData, setCardData] = useState(null)
	// const [token, setToken] = useState(null)
	//
	// useEffect(() => {
	// 	async function fetchData(token) {
	// 		try {
	// 			const response = await token
	// 			setToken(response)
	// 		} catch (error) {
	// 			console.error(error)
	// 		}
	// 	}
	//
	// 	let ignore = fetchData(getToken)
	// })

	useEffect(() => {
		const fetchData = async function () {
			try {
				const access = await getCards(token)
				setCardData(access)
			} catch (error) {
				console.error('Error fetching card data:', error)
			}
		}

		let ignore = fetchData()
	}, [token])

	return <>{cardData && <CardItem cardData={cardData} />}</>
}
