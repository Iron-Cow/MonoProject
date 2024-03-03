export const CardItem = function ({ cardData }) {
	return (
		<div>
			<table className='table'>
				<thead className='table__head'>
					<tr key={1} className='table__row'>
						<th className='table__title'>№</th>
						<th className='table__title'>Type</th>
						<th className='table__title'>Balance</th>
						<th className='table__title'>Currency</th>
						<th className='table__title'>Credit limit</th>
					</tr>
				</thead>
				<tbody className='table__body'>
					{cardData.map(
						({ id, type, currency, balance, credit_limit }, index) => (
							<tr className='table__body_tr' key={index}>
								<td className='table__description'>{index + 1}</td>
								<td className='table__description'>{type}</td>
								<td className='table__description'>
									{(balance / 100).toFixed(2)}
								</td>
								<td className='table__description'>{currency.name}</td>
								<td className='table__description'>
									{credit_limit.toFixed(2)}
								</td>
							</tr>
						)
					)}
				</tbody>
			</table>
		</div>
	)
}
