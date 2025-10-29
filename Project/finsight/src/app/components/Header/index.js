import styles from './Header.module.css';

export default function Header() {
    return (
        <header className={styles.header}>
            <div className={styles.container}>
                <div className={styles.website}>
                    <h1>FinSight</h1>
                </div>

                <nav className={styles.nav}>
                    <a href="/About">About</a>
                    <a href="/portfolio-tracker">Portfolio Tracker</a>
                    <a href="/model-insights">Model Insights</a>
                </nav>

                <div className={styles.searchBar}>
                    <input type ="text" placeholder="Search" />
                </div>

                <div className={styles.logo}>
                Logo
                </div>
            </div>
        </header>
    );
}