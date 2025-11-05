import './IndexPerformance.css';

export default function IndexPerformance() {
  return (
    <div className="indexContainer">
      <h2 className="indexTitle">Index Performance</h2>
      <div className="indexTableWrapper">
        <table className="indexTable">
          <thead>
            <tr>
              <th>Index</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>S&amp;P 500</td>
              <td className="positive">+0.5%</td>
            </tr>
            <tr>
              <td>NASDAQ</td>
              <td className="negative">-1.3%</td>
            </tr>
            <tr>
              <td>Dow Jones</td>
              <td className="positive">+6%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
