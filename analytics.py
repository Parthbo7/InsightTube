


def calculate_video_metrics(video, subscriber_count):

    view_count = int(video.get("view_count", 0))
    like_count = int(video.get("like_count", 0))
    comment_count = int(video.get("comment_count", 0))

    if view_count > 0:
        like_ratio = (like_count / view_count) * 100
        comment_ratio = (comment_count / view_count) * 100
        total_engagement_rate = ((like_count + comment_count) / view_count) * 100
        engagement_per_1000 = ((like_count + comment_count) / view_count) * 1000
    else:
        like_ratio = 0
        comment_ratio = 0
        total_engagement_rate = 0
        engagement_per_1000 = 0

    if subscriber_count > 0:
        view_subscriber_ratio = (view_count / subscriber_count) * 100
    else:
        view_subscriber_ratio = 0

    if comment_count > 0:
        like_comment_ratio = like_count / comment_count
    else:
        like_comment_ratio = 0

    return {
        "like_ratio": like_ratio,
        "comment_ratio": comment_ratio,
        "total_engagement_rate": total_engagement_rate,
        "view_subscriber_ratio": view_subscriber_ratio,
        "engagement_per_1000": engagement_per_1000,
        "like_comment_ratio": like_comment_ratio
    }


def update_channel_avg_engagement(supabase, channel_id):

    response = (
        supabase
        .table("video_analytics")
        .select("total_engagement_rate")
        .eq("channel_id", channel_id)
        .execute()
    )

    rates = [
        v["total_engagement_rate"] 
        for v in response.data 
        if v["total_engagement_rate"] is not None
    ]

    if rates:
        avg_engagement = sum(rates) / len(rates)
    else:
        avg_engagement = 0

    supabase.table("channel_info") \
        .update({"avg_engagement_rate": avg_engagement}) \
        .eq("channel_id", channel_id) \
        .execute()

    print("✅ Channel average engagement updated.")
