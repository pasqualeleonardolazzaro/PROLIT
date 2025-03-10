
import pandas as pd

def run_pipeline(args, tracker) -> None:

    input_path = args.dataset

    df = pd.read_csv(input_path, header=0)

    if args.frac != 0.0:
        df = df.sample(frac=args.frac)

    # Subscribe dataframe
    df = tracker.subscribe(df)
    tracker.analyze_changes(df)

    # Drop unnecessary columns
    cols_to_drop = ['Name', 'Ticket', 'Cabin']
    df = df.drop(cols_to_drop, axis=1)
    tracker.analyze_changes(df)

    # Fill missing values in Embarked column
    df['Embarked'] = df['Embarked'].fillna('S')
    tracker.analyze_changes(df)

    # Fill missing values in Age column with median age
    median_age = df['Age'].median()
    df['Age'] = df['Age'].fillna(median_age)
    tracker.analyze_changes(df)

    # One-hot encode categorical columns
    categorical_cols = ['Pclass', 'Sex', 'Embarked']
    for col in categorical_cols:
        dummies = pd.get_dummies(df[col], prefix=col)
        df = df.join(dummies).drop(col, axis=1)
    tracker.analyze_changes(df)
