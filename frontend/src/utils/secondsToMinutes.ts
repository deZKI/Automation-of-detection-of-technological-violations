export function secondsToMinutes(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  const formattedMinutes = minutes.toString();
  const formattedSeconds = remainingSeconds < 10 ? '0' + remainingSeconds.toString() : remainingSeconds.toString();
  
  return `${formattedMinutes}:${formattedSeconds}`;
}
