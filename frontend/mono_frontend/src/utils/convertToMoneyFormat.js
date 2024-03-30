export const convertToMoneyFormat = function (integer) {
	if (integer === 0) {
		return integer.toFixed(2)
	}
	return (integer / 100).toFixed(2)
}
