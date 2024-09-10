import {useState, useEffect} from 'react';
import {BookUp, GitMerge, GitPullRequestArrow} from "lucide-react";

const App = () => {
  const [events, setEvents] = useState([]);
  const [lastEventId, setLastEventId] = useState();
  const backendURL = import.meta.env.VITE_BACKEND_URL;

  useEffect(() => {
    const fetchEvents = async () => {
      let currentLastEventId = lastEventId;

      // If currentLastEventId is not set this means page is refreshed or new,
      // so get it from localStorage
      if (!currentLastEventId) {
        currentLastEventId = localStorage.getItem('last_event_id');  // Null if not found
      }

      const url = new URL("/webhook/get-events", backendURL);
      if (currentLastEventId) {
        url.searchParams.append('last_event_id', currentLastEventId);
      }
      const response = await fetch(url);
      const data = await response.json();

      // Update the events list and set the new lastEventId
      if (data.length > 0) {
        const latestEventId = data[0]._id;
        setEvents(data);
        setLastEventId(latestEventId);
        localStorage.setItem('last_event_id', latestEventId);
      } else {
        setEvents([]);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 15000);  // Poll every 15 seconds

    return () => {
      clearInterval(interval);
    };
  }, [backendURL]);


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
