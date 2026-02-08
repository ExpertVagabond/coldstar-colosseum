import { Composition } from "remotion";
import { ColdstarVideo } from "./ColdstarVideo";
import { ColdstarVertical } from "./ColdstarVertical";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Main video - 60 seconds at 30fps */}
      <Composition
        id="ColdstarVideo"
        component={ColdstarVideo}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* Square version for Twitter/X */}
      <Composition
        id="ColdstarSquare"
        component={ColdstarVideo}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1080}
      />

      {/* Vertical for TikTok/Reels - 18 seconds */}
      <Composition
        id="ColdstarVertical"
        component={ColdstarVertical}
        durationInFrames={540}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
