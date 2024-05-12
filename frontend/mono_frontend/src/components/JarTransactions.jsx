import {convertToMoneyFormat} from "../utils/convertToMoneyFormat";
import React from 'react';

export function JarTransactions({jarTransactions, isModalOpened, setShowModal}) {
    const closeModal = () => {
        setShowModal(false);
    };
    jarTransactions = jarTransactions || [] // null or undefined

    return (
        <>

            {isModalOpened && (
                <div>
                    <div className="modal">
                        <div className="modal-content">
                            <span className="close" onClick={closeModal}>×</span>
                            <h2>Jar Transactions</h2>
                            <div data-testid="transactions-container" className='transaction-container'>
                                {jarTransactions.map((tr, index) => (
                                    <div className={`transaction-box ${tr.amount > 0 ? "income" : "spend"}`}
                                         key={index}>
                                        <details>
                                            <summary>
                                                <span className="category-symbol">{tr.category_symbol}</span>
                                                <span className="category-name">{tr.category}</span>
                                                <span
                                                    className="amount">{convertToMoneyFormat(tr?.amount) + ' ' + tr?.currency.symbol}</span>
                                            </summary>
                                            <div className='transaction-text'>
                                                {tr.description} [Залишок {convertToMoneyFormat(tr?.balance) + ' ' + tr?.currency.symbol}]
                                            </div>
                                        </details>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

            )}
        </>
    );
}
