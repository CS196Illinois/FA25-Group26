'use client';

import { useEffect, useState} from 'react';
import styles from './Sentiment.module.css'; 

export default function SentimentSignals() {

    const [sentimentData, setsentimentData] = useState([
        {stock: 'TSLA', sentiment: '+', source: 'Twitter', timestamp: '1 min'},
        {stock: 'NFLX', sentiment: '-', source: 'Analyst', timestamp: '30 min'},
        {stock: 'GOOG', sentiment: '-', source: 'News', timestamp: '2 hours'},
        {stock: 'AMZN', sentiment: '+', source: 'Analyst', timestamp: '1 Day'},
    ]); 


    return (
        <div className={styles.sentimentContainer}>
            <h2 className={styles.title}>Sentiment Signals</h2>
            
            <div className={styles.tableWrapper}>
                <table className={styles.sentimentTable}>
                    <thead>
                        <tr>
                            <th>Stock</th>
                            <th>Sentiment</th>
                            <th>Source</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sentimentData.map((signal, index) => (
                            <tr key={index}>
                                <td>{signal.stock}</td>
                                <td className={signal.sentiment === '+' ? styles.positive : styles.negative}>
                                    {signal.sentiment}
                                </td>
                                <td>{signal.source}</td>
                                <td>{signal.timestamp}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}