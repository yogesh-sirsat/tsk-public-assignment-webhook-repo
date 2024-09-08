import {useState, useEffect} from 'react';
import {BookUp, GitMerge, GitPullRequestArrow} from "lucide-react";

const App = () => {
  const [events, setEvents] = useState([]);
  const [lastEventId, setLastEventId] = useState();

  useEffect(() => {
    const fetchEvents = async () => {

      // Fetch only new events since the lastEventId
      const url = new URL('http://localhost:5000/webhook/get-events');
      if (lastEventId) {
        url.searchParams.append('last_event_id', lastEventId);
      }
      const response = await fetch(url);
      const data = await response.json();

      // Update the events list and set the new lastEventId
      if (data.length > 0) {
        const latestEventId = data[0]._id;
        console.log(lastEventId, latestEventId);
        if (lastEventId !== latestEventId) {
          setEvents(prevEvents => [...data, ...prevEvents]);
        }
        setLastEventId(latestEventId);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 15000); // Poll every 15 seconds

    return () => {
      clearInterval(interval);
    };
  }, [lastEventId]);


  const getPushActionString = (event) => {
    return `"${event?.author}" pushed to "${event?.to_branch}" on ${event?.timestamp}`;
  };

  const getPullRequestActionString = (event) => {
    return `"${event?.author}" submitted a pull request from "${event?.from_branch}" to "${event?.to_branch}" on ${event?.timestamp}`;
  };

  const getMergeActionString = (event) => {
    return `"${event?.author}" merged branch "${event?.from_branch}" to "${event?.to_branch}" on ${event?.timestamp}`;
  };

  return (
    <div>
      <h1>GitHub Webhook Events</h1>
      <ul className="events">
        {events.map((event, index) => (
          <li key={index} className={"event-item " + event.action}>
            {event.action === 'PUSH' ?
              <>
                <BookUp/> {getPushActionString(event)}
              </> :
              event.action === 'PULL_REQUEST' ?
                <>
                  <GitPullRequestArrow/> {getPullRequestActionString(event)}
                </> :
                event.action === 'MERGE' ?
                  <>
                    <GitMerge/> {getMergeActionString(event)}
                  </> :
                  null
            }
          </li>
        ))}
      </ul>
    </div>
  );
};

export default App;
