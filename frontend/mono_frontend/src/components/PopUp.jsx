import React from 'react'

const PopUp = ({ message, type }) => {
	return <div className={`pop-up pop-up--${type}`}>{message}</div>
}
export default PopUp
