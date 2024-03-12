export const convertProgressInPercent = function (balance, goal) {
	if (goal > 0) {
		return String(Math.round((balance / goal) * 100) + '%')
	}
	if (goal === 0) {
		return '50%'
	}
}
