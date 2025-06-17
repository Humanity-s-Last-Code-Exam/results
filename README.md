# README

## Submitting Your Results to the HLCE Leaderboard

To submit your results to the HLCE leaderboard, you need to create a Pull Request (PR) in this repository. Follow the steps below to ensure your submission is correctly formatted:

### Steps to Submit

1. **Create a Folder:**
   - Name the folder after your model, for example, `Claude-3.7-Sonnet`.
   - Inside this folder, create two subfolders: `ICPC` and `IOI`.

2. **Add Evaluation Files:**
   - In the `ICPC` folder, include the file `icpc_filter_merge_codegeneration_output_eval_all.json`. This file should contain the results generated after completing the ICPC evaluation.
   - In the `IOI` folder, include the file `ioi_xxx.jsonl`. This file should contain the results generated after completing the IOI evaluation.

3. **Create a Pull Request:**
   - Ensure your PR includes the URL of your model.
   - The PR should merge your folder and its contents into the repository.

### Example Directory Structure

```
your-model-name/
├── ICPC/
│   └── icpc_filter_merge_codegeneration_output_eval_all.json
└── IOI/
    └── ioi_xxx.jsonl
```

### Additional Notes

- Make sure all filenames and folder names are correctly spelled and formatted.
- Double-check that the results files are properly generated and contain all necessary data.

By following these guidelines, you can ensure a smooth submission process for your results to the HLCE leaderboard. Thank you for your contribution!
