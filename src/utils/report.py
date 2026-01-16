def print_video_report(
    video_id: str,
    outline: list,
    section_summaries: list,
    overall_summary: dict
):
    print("\n" + "=" * 60)
    print(f"VIDEO REPORT — {video_id}")
    print("=" * 60)

    # ---------- OUTLINE ----------
    print("\n===== OUTLINE =====")
    for sec in outline:
        print(
            f"[{sec.section_id}] "
            f"{sec.title} "
            f"({sec.start:.2f}s → {sec.end:.2f}s)"
        )

    # ---------- SECTION SUMMARIES ----------
    print("\n===== SECTION SUMMARIES =====")
    for sec in section_summaries:
        print("\n" + "-" * 50)
        print(f"[{sec['section_id']}] {sec['title']}")
        print(f"Time: {sec['start']:.2f}s → {sec['end']:.2f}s")
        print("\nSummary:")
        print(sec["summary"])

        if sec.get("key_points"):
            print("\nKey points:")
            for kp in sec["key_points"]:
                print(f"- {kp}")

    # ---------- OVERALL ----------
    print("\n" + "=" * 60)
    print("===== OVERALL SUMMARY =====")
    print(overall_summary.get("overall_summary", ""))

    if overall_summary.get("main_topics"):
        print("\nMain topics:")
        for t in overall_summary["main_topics"]:
            print(f"- {t}")

    print("=" * 60 + "\n")
