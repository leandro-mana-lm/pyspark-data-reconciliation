from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Literal, Optional, TypeVar

from ..interfaces import IDataQuery, ISavingOptions, IView

T = TypeVar('T')


@dataclass
class DataFrameViewRegistry:
    """
    Class responsible for managing the registration of DataFrame views.
    """

    task: str
    prefix: bool = True

    def combine(
        self,
        left: IView,
        right: IView,
        how: Literal['union', 'unionByName'],
        when: Literal['before', 'after'],
        target: Optional[IView] = None,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator method to combine two DataFrame views using the specified
        method.

        Args:
            left (IView): Left view configuration.
            right (IView): Right view configuration.
            how (Literal['union', 'unionByName']): Method to combine the views.
            when (Literal['before', 'after']): When to apply the combination.
            target (Optional[IView], optional): Target view configuration.
            Defaults to None.

        Returns:
            Callable[[Callable[..., T]], Callable[..., T]]: Decorated method.
        """

        def wrapper(function: Callable[..., T]) -> Callable[..., T]:
            @wraps(function)
            def decorator(cls: IDataQuery, *args: Any, **kwargs: Any) -> T:
                def combining(cls: IDataQuery) -> None:
                    dataframe_left = cls.spark.table(self.name(left))
                    dataframe_right = cls.spark.table(self.name(right))

                    union_method = getattr(dataframe_left, how)
                    cls.dataframe = union_method(dataframe_right)

                dec = self.view(target or left)
                method = dec(combining)

                def before() -> T:
                    method(cls, *args, **kwargs)
                    result = function(cls, *args, **kwargs)

                    return result

                def after() -> T:
                    result = function(cls, *args, **kwargs)
                    method(cls, *args, **kwargs)

                    return result

                result = before() if when == 'before' else after()

                return result

            return decorator

        return wrapper

    def name(self, view: IView) -> str:
        """
        Generate a view name based on the view configuration and class
        settings.

        Args:
            view (IView): View configuration.

        Returns:
            str: Generated view name.
        """

        sentinel = object()

        prefix = view.get('prefix', sentinel)
        prefix = self.prefix \
            if (prefix is sentinel or prefix is None) \
            else prefix

        view_name = f'{self.task}__' if prefix else ''
        view_name += f'{view.get("step", "")}__' if view.get('step') else ''
        view_name += view['name']

        return view_name

    def refresh(
        self,
        *views: IView,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator method to refresh the specified DataFrame views.

        Raises:
            RuntimeError: If no views are provided.

        Returns:
            Callable[[Callable[..., T]], Callable[..., T]]: Decorated method.
        """

        if not views:
            message = 'No views provided for refreshing DataFrame views.'
            raise RuntimeError(message)

        def wrapper(function: Callable[..., T]) -> Callable[..., T]:
            @wraps(function)
            def decorator(cls: IDataQuery, *args: Any, **kwargs: Any) -> T:
                for view in views:
                    if 'read' not in view:
                        cls.spark.catalog.refreshTable(self.name(view))
                        cls.spark.table(self.name(view)).count()
                        continue

                    dataframe = cls.spark.read.load(
                        path=view['read'].get('path'),
                        format=view['read'].get('format'),
                        schema=view['read'].get('schema'),
                        header=view['read'].get('header'),
                        inferSchema=view['read'].get('inferSchema'),
                        sep=view['read'].get('sep'),
                        multiLine=view['read'].get('multiLine', False),
                        pathGlobFilter=view['read'].get('pathGlobFilter', '*'),
                        url=view['read'].get('url'),
                        dbtable=view['read'].get('dbtable'),
                        user=view['read'].get('user'),
                        password=view['read'].get('password'),
                        driver=view['read'].get('driver'),
                        query=view['read'].get('query'),
                    )

                    dataframe.createOrReplaceTempView(name=self.name(view))

                result = function(cls, *args, **kwargs)

                return result

            return decorator

        return wrapper

    def save(
        self,
        options: ISavingOptions,
        enable: bool = True,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator method to save the DataFrame.

        Args:
            options (ISavingOptions): Saving options.
            enable (bool, optional): Whether to enable saving the DataFrame.
            Defaults to True.

        Returns:
            Callable[[Callable[..., T]], Callable[..., T]]: Decorated method.
        """

        def wrapper(function: Callable[..., T]) -> Callable[..., T]:
            @wraps(function)
            def decorator(cls: IDataQuery, *args: Any, **kwargs: Any) -> T:
                result = function(cls, *args, **kwargs)

                if not enable:
                    return result

                cls.dataframe.write.save(
                    path=options['path'],
                    format=options['format'],
                    mode=options['mode'],
                )

                return result

            return decorator

        return wrapper

    def view(
        self,
        view: IView
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator method to create or replace a temporary view from the
        DataFrame.

        Args:
            view (IView): View configuration.

        Returns:
            Callable[[Callable[..., T]], Callable[..., T]]: Decorated method.
        """

        def wrapper(function: Callable[..., T]) -> Callable[..., T]:
            @wraps(function)
            def decorator(cls: IDataQuery, *args: Any, **kwargs: Any) -> T:
                result = function(cls, *args, **kwargs)

                view_id = self.name(view)

                cls.dataframe \
                    .toDF(*cls.dataframe.columns) \
                    .createOrReplaceTempView(name=view_id)

                if view.get('cache', False):
                    cls.spark.catalog.cacheTable(view_id)
                    cls.spark.table(view_id).count()
                else:
                    cls.spark.catalog.uncacheTable(view_id)

                return result

            return decorator

        return wrapper
