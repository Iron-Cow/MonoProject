export const convertProgressInPercent = function (balance, goal) {
	return String(Math.round((balance / goal) * 100) + '%')
}
